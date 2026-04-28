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
  onError?: (error: unknown) => void
) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inFlightRef = useRef<MutationHandle<TResult> | null>(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      requestIdRef.current += 1;
      const requestId = requestIdRef.current;

      inFlightRef.current?.abort();

      let mutation: MutationHandle<TResult>;
      try {
        mutation = trigger(value);
      } catch (err) {
        onError?.(err);
        return;
      }

      inFlightRef.current = mutation;

      mutation
        .unwrap()
        .then((result) => {
          if (requestId === requestIdRef.current) {
            onSuccess(result);
          }
        })
        .catch((err) => {
          if (!(err instanceof DOMException && err.name === "AbortError")) {
            onError?.(err);
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
      }
    };
  }, [value, delay, trigger, onSuccess, onError]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      inFlightRef.current?.abort();
    };
  }, []);
}
