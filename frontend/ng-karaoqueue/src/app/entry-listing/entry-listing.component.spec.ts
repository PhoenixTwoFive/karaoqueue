import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EntryListingComponent } from './entry-listing.component';

describe('EntryListingComponent', () => {
  let component: EntryListingComponent;
  let fixture: ComponentFixture<EntryListingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EntryListingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EntryListingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
