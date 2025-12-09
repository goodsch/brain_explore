export interface CalibreBook {
  calibre_id: number;
  title: string;
  author: string;
  cover_url: string;
}

export const graphClient = {
  login: async () => ({ user_id: 'user-123' }),
  getBooks: async () => [],
  getBookFileUrl: (id: number) => `/books/${id}/file`,
  saveJourney: async () => {},
};
