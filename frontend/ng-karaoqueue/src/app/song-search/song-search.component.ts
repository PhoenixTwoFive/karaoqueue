import { Component, OnInit } from '@angular/core';
import { SongServiceService } from "../song-service.service";
import { Song } from '../models/song.model';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators';

@Component({
  selector: 'app-song-search',
  templateUrl: './song-search.component.html',
  styleUrls: ['./song-search.component.scss']
})
export class SongSearchComponent implements OnInit {

  private searchSub$ = new Subject<string>();

  constructor(private songServiceService: SongServiceService) { }

  songs: Array<Song> = new Array<Song>();

  updateSongs(text: string) {
    this.songServiceService.searchSongByText(text).subscribe(x => {
      console.log(x);
      this.songs = x;
    });
  }

  applyFilter(filterValue: string) {
    this.searchSub$.next(filterValue)
  }

  ngOnInit(): void {
    this.searchSub$.pipe(
      debounceTime(400),
      distinctUntilChanged()
    ).subscribe((filterValue: string) => {
      this.updateSongs(filterValue);
    });
  }

}
