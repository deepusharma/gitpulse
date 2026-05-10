import { Metadata } from "next";
import { notFound } from "next/navigation";
import { fetchPublicProfile } from "@/lib/api";
import { ProfileHeader } from "@/components/profile/ProfileHeader";
import { ProfileStats } from "@/components/profile/ProfileStats";
import { TopReposList } from "@/components/profile/TopReposList";
import { RecentSummaryCard } from "@/components/profile/RecentSummaryCard";

interface ProfilePageProps {
  params: { username: string };
}

export async function generateMetadata({
  params,
}: ProfilePageProps): Promise<Metadata> {
  try {
    const profile = await fetchPublicProfile(params.username);
    const title = `${profile.username} on GitPulse`;
    const description = profile.bio || `Developer profile with ${profile.current_streak}d commit streak.`;

    return {
      title,
      description,
      openGraph: {
        title,
        description,
        type: "profile",
        images: [profile.avatar_url],
      },
      twitter: {
        card: "summary",
        title,
        description,
        images: [profile.avatar_url],
      },
    };
  } catch {
    return {
      title: "Profile Not Found | GitPulse",
      description: "This developer profile could not be found.",
    };
  }
}

export default async function ProfilePage({ params }: ProfilePageProps) {
  let profile;
  try {
    profile = await fetchPublicProfile(params.username);
  } catch (error) {
    if (error instanceof Error && error.message === "Profile not found") {
      notFound();
    }
    return (
      <div className="container mx-auto max-w-4xl px-4 py-12">
        <div className="p-6 rounded-2xl border border-destructive/20 bg-destructive/5 text-destructive">
          <h1 className="text-xl font-bold mb-2">Error Loading Profile</h1>
          <p>We encountered an issue fetching the profile. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-12 flex flex-col gap-6">
      <ProfileHeader profile={profile} />
      <ProfileStats profile={profile} />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TopReposList repos={profile.top_repos} />
        <RecentSummaryCard summary={profile.recent_summary} />
      </div>
    </main>
  );
}
