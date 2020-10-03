import DataStoredInToken from "../interfaces/dataStoredInToken.interface";
import User from "../interfaces/user.interface";
import * as jwt from 'jsonwebtoken';

export class JwtMiddleware {
    public createToken(user: User): string {
        /* expiresIn is in seconds. We take the env value which is in minutes and multiply it by 60.*/
        const expiresIn = parseInt(process.env.KQUEUE_JWTEXPIRY,10) * 60;
        const secret = process.env.KQUEUE_JWTSECRET;
        const dataStoredInToken: DataStoredInToken = {
            _id: user.username,
        };
        return jwt.sign(dataStoredInToken, secret, { expiresIn });
    }
}