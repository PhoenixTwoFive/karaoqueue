import { EntryListingComponent } from './entry-listing/entry-listing.component';
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SongSearchComponent } from './song-search/song-search.component';


const routes: Routes = [
  {path: '', component: EntryListingComponent },
  {path: 'songs', component: SongSearchComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
