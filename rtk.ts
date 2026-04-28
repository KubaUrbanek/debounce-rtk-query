import { useEffect, useRef } from "react";

type MutationTrigger<TArg, TResult> = (
  arg: TArg
) => {
  abort: () => void;
  unwrap: () => Promise<TResult>;
};

export function useDebouncedMutation<TArg, TResult>(
  value: TArg,
  delay: number,
  trigger: MutationTrigger<TArg, TResult>,
  onSuccess: (result: TResult) => void,
  options?: {
    enabled?: boolean;
    skipIf?: (value: TArg) => boolean;
  }
) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inFlightRef = useRef<ReturnType<MutationTrigger<TArg, TResult>> | null>(null);
  const requestIdRef = useRef(0);

  useEffect(() => {
    if (options?.enabled === false) return;
    if (options?.skipIf?.(value)) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      requestIdRef.current += 1;
      const requestId = requestIdRef.current;

      // cancel previous request
      if (inFlightRef.current) {
        inFlightRef.current.abort();
      }

      const promise = trigger(value);
      inFlightRef.current = promise;

      promise
        .unwrap()
        .then((result) => {
          if (requestId === requestIdRef.current) {
            onSuccess(result);
          }
        })
        .catch(() => {
          // ignore abort errors silently
        });
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, delay, trigger, onSuccess, options]);
}
