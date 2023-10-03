import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SongChipComponent } from './song-chip.component';

describe('SongChipComponent', () => {
  let component: SongChipComponent;
  let fixture: ComponentFixture<SongChipComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SongChipComponent]
    });
    fixture = TestBed.createComponent(SongChipComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
