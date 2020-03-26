export class Genre {

  constructor(id: number, name: string) {
    this.id = id;
    this._name = name;
  }


  public get name() : string {
    return this._name;
  }


  id: number;
  _name: string;
}
