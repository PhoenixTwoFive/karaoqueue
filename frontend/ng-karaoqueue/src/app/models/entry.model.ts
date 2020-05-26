export class Entry {

  constructor(singer_name: string, song: string, auth_cookie?: string) {
    this.singer_name=singer_name;
    this.song=song;
    this.auth_cookie = auth_cookie;
  }

  singer_name: string;
  song: string; //Actually the ID of the Song
  auth_cookie?: string; //The "cookie" to authenticate for changing an entry. Null otherwise
}
