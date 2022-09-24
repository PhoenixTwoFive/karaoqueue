import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
 
import { Entry } from './models/entry.model';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EntryServiceService {

  private api: string;
  constructor(
    private http: HttpClient,
    private configSvc: RuntimeConfigLoaderService
  ) {
    this.api = configSvc.getConfigObjectKey("api");
  }

  getEntries(): Observable<Array<Entry>> {
      return null; // TODO
  }


}
