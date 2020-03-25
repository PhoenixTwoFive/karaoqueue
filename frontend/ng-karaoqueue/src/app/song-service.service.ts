import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Song } from './models/song.model';

@Injectable({
  providedIn: 'root'
})
export class SongServiceService {

  constructor(
    private http: HttpClient
  ) {}

  searchSongByText(text:string):Array<Song> {
      return [new Song()];
  }
}
