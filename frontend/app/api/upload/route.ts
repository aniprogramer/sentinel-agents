import { NextResponse } from 'next/server';

async function fetchGitMeta(owner: string, repo: string) {
	const headers: Record<string, string> = { Accept: 'application/vnd.github.v3+json' };

	const commitRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/commits?per_page=1`, { headers });
	if (!commitRes.ok) return { ok: false, error: 'Failed to fetch commits' };
	const commits = await commitRes.json();
	const commit = commits?.[0]?.sha ?? null;
	const commitMessage = commits?.[0]?.commit?.message ?? null;
	const commitDate = commits?.[0]?.commit?.author?.date ?? null;

	const prsRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/pulls?per_page=5&state=all`, { headers });
	const prs = prsRes.ok ? await prsRes.json() : [];
	const latestPr = prs?.[0] ? { number: prs[0].number, title: prs[0].title, url: prs[0].html_url } : null;

	return { ok: true, commit, commitMessage, commitDate, pr: latestPr };
}

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const repoUrl = body.repoUrl;

        // 1. Fetch GitHub Meta for the UI Sidebar
        let repoMeta = null;
        if (repoUrl && repoUrl.includes('github.com')) {
            const match = repoUrl.match(/github\.com\/(.+?)\/(.+?)(?:\.git|\/|$)/i);
            if (match) {
                const metaResult = await fetchGitMeta(match[1], match[2]);
                if (metaResult.ok) {
                    repoMeta = {
                        owner: match[1],
                        repo: match[2],
                        commit: metaResult.commit,
                        commitMessage: metaResult.commitMessage,
                        commitDate: metaResult.commitDate,
                        pr: metaResult.pr
                    };
                }
            }
        }

        // 2. Call the new FastAPI streaming endpoint
        const backendBase = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000';
        const response = await fetch(`${backendBase}/orchestrator/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target: repoUrl, action: 'scan' })
        });

        if (!response.body) throw new Error("No response body from backend");

        // 3. Create a TransformStream to inject the GitHub Meta first, then pipe the logs
        const transformStream = new TransformStream({
            start(controller) {
                if (repoMeta) {
                    // Inject metadata so page.tsx can render the sidebar
                    const metaChunk = JSON.stringify({ 
                        repoMeta, 
                        msg: "System: Target locked. Git metadata synced.", 
                        type: "sys" 
                    }) + "\n";
                    controller.enqueue(new TextEncoder().encode(metaChunk));
                }
            }
        });

        return new Response(response.body.pipeThrough(transformStream), {
            headers: {
                'Content-Type': 'application/x-ndjson',
                'Cache-Control': 'no-cache'
            }
        });

    } catch (err: any) {
        return NextResponse.json({ success: false, message: String(err) }, { status: 500 });
    }
}

export const runtime = 'edge';
