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
		const contentType = req.headers.get('content-type') || '';

		if (contentType.includes('application/json')) {
			const body = await req.json();
			const { repoUrl } = body;
			if (!repoUrl) return NextResponse.json({ success: false, message: 'repoUrl required' }, { status: 400 });

			// extract owner/repo from common GitHub URL patterns
			const match = repoUrl.match(/github\.com\/(.+?)\/(.+?)(?:\.git|\/|$)/i);
			if (!match) return NextResponse.json({ success: false, message: 'invalid github url' }, { status: 400 });
			const owner = match[1];
			const repo = match[2];

			const meta = await fetchGitMeta(owner, repo);
			if (!meta.ok)
				return NextResponse.json({ success: false, message: meta.error || 'gitmeta failed' }, { status: 502 });

			return NextResponse.json({
				success: true,
				data: {
					owner,
					repo,
					commit: meta.commit,
					commitMessage: meta.commitMessage,
					commitDate: meta.commitDate,
					pr: meta.pr,
				},
			});
		}

		// If multipart form (file upload), forward to backend service
		if (contentType.includes('multipart/form-data')) {
			const form = await req.formData();
			const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000/api/code/upload';

			const forwardRes = await fetch(backendUrl, { method: 'POST', body: form as unknown as BodyInit });
			const json = await forwardRes.json().catch(() => null);
			return NextResponse.json({ success: forwardRes.ok, status: forwardRes.status, data: json });
		}

		return NextResponse.json({ success: false, message: 'unsupported content type' }, { status: 415 });
	} catch (err: any) {
		return NextResponse.json({ success: false, message: String(err) }, { status: 500 });
	}
}

export const runtime = 'edge';
