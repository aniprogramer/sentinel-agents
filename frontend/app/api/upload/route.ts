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
		const backendBase = process.env.BACKEND_URL ?? 'http://localhost:8000';

		const url = new URL(req.url);
		// determine action by path segment after /api/upload
		const suffix = url.pathname.replace(/\/api\/upload/i, '') || '/';

		// normalize suffix to one of allowed endpoints
		const allowed = ['/', '/webhook/github', '/analyze', '/generate_poe', '/generate_patch', '/verify'];
		let targetPath = '/';
		if (allowed.includes(suffix)) targetPath = suffix;

		const contentType = req.headers.get('content-type') || '';

		// If GET-like root behavior required (but this is POST handler) still handle '/'
		if (targetPath === '/' && contentType.includes('application/json')) {
			// fallback: if body has repoUrl, return git metadata without forwarding
			const body = await req.json().catch(() => null);
			if (body?.repoUrl) {
				const match = body.repoUrl.match(/github\.com\/(.+?)\/(.+?)(?:\.git|\/|$)/i);
				if (!match)
					return NextResponse.json({ success: false, message: 'invalid github url' }, { status: 400 });
				const owner = match[1];
				const repo = match[2];
				const meta = await fetchGitMeta(owner, repo);
				if (!meta.ok)
					return NextResponse.json(
						{ success: false, message: meta.error || 'gitmeta failed' },
						{ status: 502 }
					);
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
		}

		// Determine backend target for forwarding
		// If the caller used a query param `action`, prefer that
		const action = url.searchParams.get('action');
		if (action && allowed.includes(`/${action}`)) targetPath = `/${action}`;

		// If JSON body specifies an `action` field, use it
		let jsonBody: any = null;
		if (contentType.includes('application/json')) {
			jsonBody = await req.json().catch(() => null);
			if (jsonBody?.action && allowed.includes(`/${jsonBody.action}`)) targetPath = `/${jsonBody.action}`;
		}

		// Handle root POST: return helpful message
		if (targetPath === '/' && req.method === 'POST' && !contentType.includes('multipart/form-data')) {
			return NextResponse.json({
				success: true,
				message: 'Upload API root. Use /analyze, /generate_poe, /generate_patch, /verify or /webhook/github',
			});
		}

		// Forward the request to backend endpoint
		const backendUrl = `${backendBase}${targetPath}`;

		// For multipart/form-data forward form directly
		if (contentType.includes('multipart/form-data')) {
			const form = await req.formData();
			const forwardRes = await fetch(backendUrl, { method: 'POST', body: form as unknown as BodyInit });
			const json = await forwardRes.json().catch(() => null);
			return NextResponse.json({ success: forwardRes.ok, status: forwardRes.status, data: json });
		}

		// For JSON or other bodies, forward JSON
		const forwardRes = await fetch(backendUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(jsonBody ?? {}),
		});
		const respJson = await forwardRes.json().catch(() => null);
		return NextResponse.json({ success: forwardRes.ok, status: forwardRes.status, data: respJson });
	} catch (err: any) {
		return NextResponse.json({ success: false, message: String(err) }, { status: 500 });
	}
}

export const runtime = 'edge';
