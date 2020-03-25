import { TestBed } from '@angular/core/testing';

import { EntryServiceService } from './entry-service.service';

describe('EntryServiceService', () => {
  let service: EntryServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EntryServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
