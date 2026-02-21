'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { Activity, FileCode, GitBranch, Lock, Search, ShieldCheck, Terminal, Zap } from 'lucide-react';
import React, { useEffect, useMemo, useRef, useState } from 'react';

// --- Types ---
interface LogEntry {
	msg: string;
	type: 'sys' | 'audit' | 'red' | 'red_alert' | 'blue' | 'verify' | 'sys_green';
	time: string;
}

interface AgentProps {
	icon: React.ReactNode;
	name: string;
	color: string;
	status: string;
	isActive: boolean;
}

export default function HomePage() {
	const [repoUrl, setRepoUrl] = useState('');
	const [isAnalyzing, setIsAnalyzing] = useState(false);
	const [logs, setLogs] = useState<LogEntry[]>([
		{ msg: 'System: Awaiting target handshake...', type: 'sys', time: new Date().toISOString() },
	]);
	const logEndRef = useRef<HTMLDivElement>(null);

	const [repoMeta, setRepoMeta] = useState<{
		owner?: string;
		repo?: string;
		commit?: string | null;
		commitMessage?: string | null;
		commitDate?: string | null;
		pr?: { number: number; title?: string; url?: string } | null;
	} | null>(null);

	// Derived state to highlight cards based on the latest log type
	const activeAgent = useMemo(() => {
		if (!isAnalyzing) return null;
		const lastType = logs[logs.length - 1]?.type;
		if (lastType === 'audit') return 'AUDITOR';
		if (lastType === 'red' || lastType === 'red_alert') return 'RED TEAM';
		if (lastType === 'blue' || lastType === 'verify') return 'BLUE TEAM';
		return null;
	}, [logs, isAnalyzing]);

	useEffect(() => {
		logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
	}, [logs]);

	const appendLog = (entry: { msg: string; type?: LogEntry['type']; time?: string }) => {
		const e: LogEntry = {
			msg: entry.msg,
			type: entry.type ?? 'sys',
			time: entry.time ?? new Date().toISOString(),
		};
		setLogs((prev) => [...prev, e]);
	};

	const runDemo = async () => {
		if (isAnalyzing) return;
		setLogs([
			{ msg: 'System: Initializing multi-agent orchestration...', type: 'sys', time: new Date().toISOString() },
		]);
		setIsAnalyzing(true);

		try {
			const res = await fetch(`/api/upload?action=analyze`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ repoUrl, action: 'analyze' }),
			});

			if (!res.ok) {
				const txt = await res.text().catch(() => String(res.status));
				appendLog({ msg: `Error: ${res.status} ${txt}`, type: 'sys' });
				setIsAnalyzing(false);
				return;
			}

			const ct = res.headers.get('content-type') || '';
			// If backend returned JSON (final snapshot), handle gracefully
			if (ct.includes('application/json')) {
				const json = await res.json().catch(() => null);
				if (json?.success && json.data?.owner) {
					setRepoMeta({
						owner: json.data.owner,
						repo: json.data.repo,
						commit: json.data.commit,
						commitMessage: json.data.commitMessage,
						commitDate: json.data.commitDate,
						pr: json.data.pr,
					});
				}
				// If the JSON contains logs array, append them
				if (Array.isArray(json?.logs)) {
					json.logs.forEach((l: any) =>
						appendLog({ msg: l.msg ?? JSON.stringify(l), type: l.type ?? 'sys', time: l.time })
					);
				}
				setIsAnalyzing(false);
				return;
			}

			// Otherwise attempt to stream text/NDJSON
			const reader = res.body?.getReader();
			if (!reader) {
				appendLog({ msg: 'No stream available from server.', type: 'sys' });
				setIsAnalyzing(false);
				return;
			}

			const dec = new TextDecoder();
			let buffer = '';
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += dec.decode(value, { stream: true });
				const parts = buffer.split('\n');
				buffer = parts.pop() ?? '';
				for (const part of parts) {
					if (!part.trim()) continue;
					try {
						const obj = JSON.parse(part);
						if (obj.repoMeta) setRepoMeta(obj.repoMeta);
						appendLog({ msg: obj.msg ?? JSON.stringify(obj), type: obj.type ?? 'sys', time: obj.time });
					} catch {
						appendLog({ msg: part, type: 'sys' });
					}
				}
			}

			if (buffer.trim()) {
				try {
					const obj = JSON.parse(buffer);
					appendLog({ msg: obj.msg ?? JSON.stringify(obj), type: obj.type ?? 'sys', time: obj.time });
				} catch {
					appendLog({ msg: buffer, type: 'sys' });
				}
			}
		} catch (err: any) {
			appendLog({ msg: `Stream error: ${String(err)}`, type: 'sys' });
		} finally {
			setIsAnalyzing(false);
		}
	};

	return (
		<main className="min-h-screen bg-[#03060b] text-slate-200 selection:bg-blue-500/40 overflow-x-hidden font-sans">
			{/* Dynamic Background */}
			<div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(17,24,39,1)_0%,rgba(2,4,10,1)_100%)] -z-10" />
			<div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-125 bg-blue-600/10 blur-[120px] rounded-full opacity-50 pointer-events-none" />

			<section className="relative max-w-7xl mx-auto py-20 px-6">
				<div className="flex flex-col lg:flex-row gap-16 items-start">
					{/* Left Column: Hero */}
					<div className="flex-1 space-y-8 lg:sticky lg:top-20">
						<div className="space-y-4">
							<Badge
								variant="outline"
								className="bg-blue-950/30 text-blue-400 border-blue-500/30 px-4 py-1.5 backdrop-blur-md"
							>
								<Activity className="w-3.5 h-3.5 mr-2 animate-pulse" />
								<span className="tracking-widest text-[10px] font-bold">VEX-STORM CORE ACTIVE</span>
							</Badge>

							<h1 className="text-6xl md:text-8xl font-black tracking-tight leading-[0.9] text-white">
								DEFEND <br />
								<span className="text-transparent bg-clip-text bg-linear-to-r from-blue-400 to-indigo-600">
									AUTONOMOUSLY
								</span>
							</h1>

							<p className="text-xl text-slate-400 max-w-lg leading-relaxed font-light">
								Stop guessing. Start proving. Our agents{' '}
								<span className="text-white font-medium italic">attack</span> your code to ensure your
								patches actually work.
							</p>
						</div>

						<div className="group relative flex flex-col sm:flex-row gap-3 p-3 bg-white/3 border border-white/10 rounded-2xl backdrop-blur-xl transition-all hover:border-white/20">
							<div className="flex-1 flex items-center px-4 gap-3">
								<Search className="w-5 h-5 text-slate-500" />
								<Input
									placeholder="Paste GitHub repository URL..."
									value={repoUrl}
									onChange={(e) => setRepoUrl(e.target.value)}
									className="bg-transparent border-none focus-visible:ring-0 text-md h-12 p-0 placeholder:text-slate-600"
								/>
							</div>
							<Button
								onClick={runDemo}
								disabled={isAnalyzing}
								className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-10 h-14 rounded-xl shadow-lg shadow-blue-900/20 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50"
							>
								{isAnalyzing ? 'ORCHESTRATING...' : 'SECURE REPO'}
							</Button>
						</div>
					</div>

					{/* Right Column: Status Cards */}
					<div className="w-full lg:w-80 space-y-4">
						<AgentCard
							icon={<Search />}
							name="AUDITOR"
							color="text-amber-400"
							status={
								isAnalyzing ? (activeAgent === 'AUDITOR' ? 'Analyzing AST...' : 'Standby') : 'Ready'
							}
							isActive={activeAgent === 'AUDITOR'}
						/>
						<AgentCard
							icon={<Zap />}
							name="RED TEAM"
							color="text-rose-500"
							status={
								isAnalyzing
									? activeAgent === 'RED TEAM'
										? 'Exploiting...'
										: 'Calculating...'
									: 'Ready'
							}
							isActive={activeAgent === 'RED TEAM'}
						/>
						<AgentCard
							icon={<ShieldCheck />}
							name="BLUE TEAM"
							color="text-emerald-400"
							status={
								isAnalyzing
									? activeAgent === 'BLUE TEAM'
										? 'Synthesizing...'
										: 'Awaiting PoE'
									: 'Ready'
							}
							isActive={activeAgent === 'BLUE TEAM'}
						/>
					</div>
				</div>

				{/* War Room & Console */}
				<div className="mt-24 grid grid-cols-1 lg:grid-cols-12 gap-8">
					<Card className="lg:col-span-8 bg-[#05070a]/80 border-white/5 backdrop-blur-2xl shadow-3xl rounded-3xl overflow-hidden">
						<div className="bg-white/2 px-6 py-4 border-b border-white/5 flex items-center justify-between">
							<div className="flex gap-2">
								<div className="w-3 h-3 rounded-full bg-green-400" />
								<div className="w-3 h-3 rounded-full bg-amber-400" />
								<div className="w-3 h-3 rounded-full bg-red-400" />
							</div>
							<div className="flex items-center gap-2">
								<Terminal className="w-3 h-3 text-blue-500" />
								<span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
									Live_Execution_Trace.sh
								</span>
							</div>
						</div>
						<CardContent className="p-0">
							<div className="h-112.5 overflow-y-auto p-8 font-mono text-sm space-y-4 custom-scrollbar bg-linear-to-b from-transparent to-blue-900/5">
								{logs.map((log, i) => (
									<div
										key={i}
										className="flex gap-5 animate-in fade-in slide-in-from-bottom-1 duration-500"
									>
										<span className="text-slate-700 shrink-0 tabular-nums">
											{new Date(log.time).toLocaleTimeString([], {
												hour12: false,
												minute: '2-digit',
												second: '2-digit',
											})}
										</span>
										<span
											className={cn(
												'leading-relaxed',
												log.type === 'red_alert' &&
													'text-rose-500 font-bold drop-shadow-[0_0_8px_rgba(244,63,94,0.3)]',
												log.type === 'sys_green' && 'text-emerald-400 font-bold',
												log.type === 'audit' && 'text-amber-200/90',
												log.type === 'red' && 'text-rose-400/80',
												log.type === 'blue' && 'text-blue-400',
												log.type === 'verify' && 'text-indigo-400',
												log.type === 'sys' && 'text-slate-500 italic'
											)}
										>
											{log.msg}
										</span>
									</div>
								))}
								<div ref={logEndRef} />
							</div>
						</CardContent>
					</Card>

					{/* Evidence / Stats Sidebar */}
					<div className="lg:col-span-4 space-y-8">
						<div>
							<h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-6">
								Evidence Pipeline
							</h3>
							<div className="space-y-3">
								<EvidenceItem
									icon={<FileCode />}
									label="Source AST"
									detail="Vulnerability Context"
									isActive={isAnalyzing}
								/>
								<EvidenceItem
									icon={<Lock />}
									label="Attack Vector"
									detail="PoE Payload Verified"
									isActive={isAnalyzing}
								/>
								{repoMeta?.pr ? (
									<EvidenceItem
										icon={<GitBranch />}
										label={`PR #${repoMeta.pr.number}`}
										detail={repoMeta.pr.title ?? 'Automated Patch'}
										isActive={!isAnalyzing && logs.length > 5}
									/>
								) : null}
								{repoMeta?.commit ? (
									<EvidenceItem
										icon={<FileCode />}
										label={`commit ${repoMeta.commit.slice(0, 7)}`}
										detail={
											repoMeta.commitMessage
												? repoMeta.commitMessage.split('\n')[0]
												: 'Latest commit'
										}
										isActive={!isAnalyzing && logs.length > 5}
									/>
								) : null}
								{!repoMeta?.pr && !repoMeta?.commit ? (
									<EvidenceItem
										icon={<GitBranch />}
										label="PR / Commit"
										detail="Automated Patch"
										isActive={!isAnalyzing && logs.length > 5}
									/>
								) : null}
							</div>
						</div>

						{/*
						<div className="p-8 rounded-3xl bg-linear-to-br from-blue-600/10 via-transparent to-transparent border border-blue-500/10">
							<div className="flex items-center gap-4 mb-4">
								<div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-500/40">
									<Cpu className="w-5 h-5 text-white" />
								</div>
								<h4 className="font-bold text-white tracking-tight">Neural Verification</h4>
							</div>
							<p className="text-sm text-slate-400 leading-relaxed">
								Every patch is cross-validated by spawning a twin-container architecture. We don't just
								fix code; we verify the fix is unhackable.
							</p>
            </div> */}
					</div>
				</div>
			</section>
		</main>
	);
}

function AgentCard({ icon, name, color, status, isActive }: AgentProps) {
	return (
		<div
			className={cn(
				'p-5 rounded-2xl border transition-all duration-500 group',
				isActive
					? 'bg-white/8 border-white/20 shadow-2xl scale-[1.02] translate-x-2'
					: 'bg-white/2 border-white/5 opacity-60'
			)}
		>
			<div className="flex items-center gap-4">
				<div
					className={cn(
						'p-2.5 rounded-xl bg-black/50 transition-colors',
						color,
						isActive && 'animate-pulse ring-2 ring-current ring-offset-2 ring-offset-black'
					)}
				>
					{icon}
				</div>
				<div className="flex-1">
					<div className="text-[9px] text-slate-500 font-black tracking-widest">{name}</div>
					<div
						className={cn(
							'text-sm font-medium transition-colors',
							isActive ? 'text-white' : 'text-slate-400'
						)}
					>
						{status}
					</div>
				</div>
			</div>
		</div>
	);
}

function EvidenceItem({
	icon,
	label,
	detail,
	isActive,
}: {
	icon: React.ReactNode;
	label: string;
	detail: string;
	isActive?: boolean;
}) {
	return (
		<div className="group flex items-center gap-4 p-4 rounded-2xl border border-white/5 bg-white/2 hover:bg-white/5 hover:border-white/10 transition-all cursor-crosshair">
			<div className="p-2 bg-black/40 rounded-lg text-slate-500 group-hover:text-blue-400 transition-colors">
				{icon}
			</div>
			<div>
				<div className="text-sm font-bold text-slate-300">{label}</div>
				<div className="text-[10px] text-slate-500 uppercase tracking-tighter">{detail}</div>
			</div>
		</div>
	);
}
