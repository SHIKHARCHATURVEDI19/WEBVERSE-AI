import { SavedVersionPreview } from "@/components/saved-version-preview";

export default async function PreviewPage({ params }: { params: Promise<{ projectId: string; versionId: string }> }) {
  const { projectId, versionId } = await params;
  return <SavedVersionPreview projectId={projectId} versionId={versionId} />;
}
