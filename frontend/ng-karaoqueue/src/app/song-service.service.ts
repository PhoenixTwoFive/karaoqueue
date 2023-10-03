import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Song } from './models/song.model';
import { Artist } from './models/artist.model';
import { Genre } from './models/genre.model';
import { Language } from './models/language.model';
 
import { ConnectableObservable, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SongServiceService {

  private api: string;
  constructor(
    private http: HttpClient,
  ) {
    // TODO: get api from config
    this.api= "http://localhost:5000/api";
  }

  searchSongByText(text: string): Observable<Array<Song>> {


    let out = new Array<Song>();

    this.http.get(this.api +"/songs/search?q="+text).subscribe((data: Observable<JSON>) => {
      data.forEach(element => {
        let styles = new Array<String>();
        let languages = new Array<String>();
        for (let style of element["styles"].split(",")) {
          styles.push(style);
        }
        for (let language of element["languages"].split(",")) {
          languages.push(language);
        }
        out.push(new Song(element["title"],element["artist"],element["karafun_id"],element["duo"],element["explicit"],element["_id"],styles,languages));
      });
      console.log(out);
    });

    const observable = new Observable<Array<Song>>( subscriber => {
      subscriber.next(out);
    })


    return observable;
  }

}
