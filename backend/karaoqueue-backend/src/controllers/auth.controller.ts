import { Post, BodyParam, Body, Res, Req, JsonController, UseBefore, Get, CookieParam } from "routing-controllers";
import { UserCredential } from "../models/usercredential.model";

@JsonController("/auth")
export class AuthenticationController {
    @Post("/login")
    doLogin(@Body() usercredential: UserCredential, @Res() res: any) {
        return "//TODO login";
    }

    @Get("/logout")
    doLogout() {
        return "//TODO logout";
    }
}