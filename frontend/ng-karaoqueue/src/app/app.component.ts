import { Component, OnInit } from '@angular/core';
import { RuntimeConfigLoaderService } from 'runtime-config-loader';
 

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit{

  constructor(private configSvc: RuntimeConfigLoaderService) {}
  ngOnInit(): void {
    console.log("API at ",this.configSvc.getConfigObjectKey("api"));
  }
  title = 'KaraoQueue';
}
