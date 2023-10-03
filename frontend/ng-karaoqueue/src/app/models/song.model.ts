import { Genre } from './genre.model';
import { Language } from './language.model';
import { Artist } from './artist.model';

export class Song {

  constructor(title: string, artist: Artist, karafun_id: number, duo: boolean, explicit: boolean, id: number, styles: Array<String>, languages: Array<String>) {
    this.title=title;
    this.artist=artist;
    this.karafun_id=karafun_id;
    this.duo=duo;
    this.explicit=explicit;
    this.id=id;
    this.styles=styles;
    this.languages=languages;
  }

  title: string;
  artist: Artist;
  karafun_id: number;
  duo: boolean;
  explicit: boolean;
  id: number;
  styles: Array<String>;
  languages: Array<String>;
}
