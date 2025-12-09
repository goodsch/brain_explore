export function useEntityLookup() {
  return {
    lookupEntity: (text: string) => console.log('Lookup:', text),
  };
}
