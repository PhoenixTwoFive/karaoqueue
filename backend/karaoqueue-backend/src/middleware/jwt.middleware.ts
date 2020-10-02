import DataStoredInToken from "../interfaces/dataStoredInToken.interface";
import User from "../interfaces/user.interface";
import * as jwt from 'jsonwebtoken';

export class JwtMiddleware {
    public createToken(user: User): string {
        const expiresIn = 60 * 60; // an hour
        const secret = process.env.KQUEUE_JWTSECRET;
        const dataStoredInToken: DataStoredInToken = {
            _id: user.username,
        };
        return jwt.sign(dataStoredInToken, secret, { expiresIn });
    }
}