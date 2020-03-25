import { Genre } from './genre.model';
import { Language } from './language.model';
import { Artist } from './artist.model';

export class Song {
  explicit: boolean;
  duet: boolean;
  title: string;
  id: number;
  karafun_id: number;
  genres: Array<Genre>;
  languages: Array<Language>;
  artist: Artist;
}
