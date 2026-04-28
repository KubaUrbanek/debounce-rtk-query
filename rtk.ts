import { useEffect, useRef } from "react";

type MutationHandle<TResult> = {
  abort: () => void;
  unwrap: () => Promise<TResult>;
};

type MutationTrigger<TArg, TResult> = (arg: TArg) => MutationHandle<TResult>;

export function useDebouncedMutation<TArg, TResult>(
  value: TArg,
  delay: number,
  trigger: MutationTrigger<TArg, TResult>,
  onSuccess: (result: TResult) => void,
  options?: {
    enabled?: boolean;
    skipIf?: (value: TArg) => boolean;
    onError?: (error: unknown) => void;
  }
) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inFlightRef = useRef<MutationHandle<TResult> | null>(null);
  const requestIdRef = useRef(0);

  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(options?.onError);

  useEffect(() => {
    onSuccessRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    onErrorRef.current = options?.onError;
  }, [options?.onError]);

  useEffect(() => {
    const enabled = options?.enabled !== false;
    const shouldSkip = options?.skipIf?.(value) ?? false;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    if (!enabled || shouldSkip) {
      inFlightRef.current?.abort();
      inFlightRef.current = null;
      return;
    }

    timeoutRef.current = setTimeout(() => {
      requestIdRef.current += 1;
      const requestId = requestIdRef.current;

      inFlightRef.current?.abort();
      inFlightRef.current = null;

      let mutation: MutationHandle<TResult>;
      try {
        mutation = trigger(value);
      } catch (error) {
        onErrorRef.current?.(error);
        return;
      }

      inFlightRef.current = mutation;

      mutation
        .unwrap()
        .then((result) => {
          if (requestId === requestIdRef.current) {
            onSuccessRef.current(result);
          }
        })
        .catch((error: unknown) => {
          if (
            !(error instanceof DOMException && error.name === "AbortError")
          ) {
            onErrorRef.current?.(error);
          }
        })
        .finally(() => {
          if (inFlightRef.current === mutation) {
            inFlightRef.current = null;
          }
        });
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };
  }, [value, delay, trigger, options?.enabled, options?.skipIf]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      inFlightRef.current?.abort();
    };
  }, []);
}
