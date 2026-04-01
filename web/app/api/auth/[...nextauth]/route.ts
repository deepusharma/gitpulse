import NextAuth from "next-auth";
import GithubProvider from "next-auth/providers/github";

const handler = NextAuth({
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_CLIENT_ID as string,
      clientSecret: process.env.GITHUB_CLIENT_SECRET as string,
      profile(profile) {
        return {
          id: profile.id.toString(),
          name: profile.name || profile.login,
          email: profile.email,
          image: profile.avatar_url,
          username: profile.login,
        };
      },
    }),
  ],
  callbacks: {
    async session({ session, token }: any) {
      if (token?.username) {
        session.user.username = token.username;
      }
      return session;
    },
    async jwt({ token, profile }: any) {
      if (profile) {
        token.username = profile.login;
      }
      return token;
    },
  },
});

export { handler as GET, handler as POST };
