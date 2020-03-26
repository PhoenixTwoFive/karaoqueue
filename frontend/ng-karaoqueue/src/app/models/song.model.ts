import { Genre } from './genre.model';
import { Language } from './language.model';
import { Artist } from './artist.model';

export class Song {

  constructor(title: string, artist: Artist, karafun_id: number, duet: boolean, explicit: boolean, id: number, genres: Array<Genre>, languages: Array<Language>) {
    this.title=title;
    this.artist=artist;
    this.karafun_id=karafun_id;
    this.duet=duet;
    this.explicit=explicit;
    this.id=id;
    this.genres=genres;
    this.languages=languages;
  }

  title: string;
  artist: Artist;
  karafun_id: number;
  duet: boolean;
  explicit: boolean;
  id: number;
  genres: Array<Genre>;
  languages: Array<Language>;
}
