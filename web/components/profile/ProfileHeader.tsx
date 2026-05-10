import Image from "next/image";
import type { PublicProfile } from "@/types/profile";

interface ProfileHeaderProps {
  profile: PublicProfile;
}

export function ProfileHeader({ profile }: ProfileHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 p-6 rounded-2xl border border-border bg-card">
      <div className="relative shrink-0">
        <Image
          src={profile.avatar_url}
          alt={`${profile.username}'s avatar`}
          width={96}
          height={96}
          className="rounded-full ring-2 ring-primary/30"
        />
        {profile.current_streak > 0 && (
          <span className="absolute -bottom-1 -right-1 bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded-full shadow">
            🔥 {profile.current_streak}d
          </span>
        )}
      </div>

      <div className="flex flex-col items-center sm:items-start gap-1 min-w-0">
        <h1 className="text-2xl font-bold tracking-tight truncate">
          {profile.username}
        </h1>
        {profile.bio && (
          <p className="text-muted-foreground text-sm leading-relaxed max-w-md">
            {profile.bio}
          </p>
        )}
        <div className="flex items-center gap-2 mt-1">
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
            <span className="font-mono text-primary">&gt;</span> gitpulse profile
          </span>
        </div>
      </div>
    </div>
  );
}
