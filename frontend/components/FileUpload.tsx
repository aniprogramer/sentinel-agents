'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { CheckCircle2, FileWarning, Loader2, UploadCloud, X } from 'lucide-react';
import React, { useState } from 'react';

interface FileUploadProps {
	uploadUrl?: string; // optional endpoint to POST the file to
	onUploadSuccess?: (filename: string) => void;
	className?: string;
}

export default function FileUpload({ uploadUrl, onUploadSuccess, className }: FileUploadProps) {
	const [file, setFile] = useState<File | null>(null);
	const [preview, setPreview] = useState<string | null>(null); // text preview for code files
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [isDragging, setIsDragging] = useState(false);

	const handleFileChange = (selectedFile: File | undefined) => {
		if (!selectedFile) return;

		const allowedExts = [
			'.js',
			'.ts',
			'.tsx',
			'.jsx',
			'.py',
			'.java',
			'.c',
			'.cpp',
			'.go',
			'.rs',
			'.json',
			'.md',
			'.sql',
			'.sh',
		];
		const name = selectedFile.name.toLowerCase();
		const matchesExt = allowedExts.some((ext) => name.endsWith(ext));
		if (!matchesExt) {
			setError('Invalid file type. Allowed: ' + allowedExts.join(', '));
			return;
		}

		if (selectedFile.size > 25 * 1024 * 1024) {
			setError('File too large. Max size is 25MB.');
			return;
		}

		setError(null);
		setFile(selectedFile);

		const reader = new FileReader();
		reader.onloadend = () => setPreview(reader.result as string);
		reader.readAsText(selectedFile);
	};

	const clearFile = (e: React.MouseEvent) => {
		e.stopPropagation();
		setFile(null);
		setPreview(null);
		setError(null);
	};

	// --- PROPER HANDLE UPLOAD ---
	async function handleUpload() {
		console.log('Triggering Code Upload...');
		if (!file) {
			console.error('No file selected');
			return;
		}

		setLoading(true);
		setError(null);

		try {
			const formData = new FormData();
			formData.append('file', file);

			const endpoint = uploadUrl ?? '/api/code/upload';
			console.log('Sending to', endpoint);

			const res = await fetch(endpoint, {
				method: 'POST',
				body: formData,
			});

			console.log('Response status:', res.status);

			const result = await res.json();
			if (!res.ok || (result && result.success === false)) {
				throw new Error(result?.message || 'Upload failed');
			}

			console.log('Upload Success:', result);
			onUploadSuccess?.(result?.data?.filename ?? file.name);
		} catch (err: any) {
			console.error('Catch block error:', err);
			setError(err?.message ?? String(err));
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className={cn('w-full max-w-md mx-auto space-y-4', className)}>
			<Card
				onDragOver={(e) => {
					e.preventDefault();
					setIsDragging(true);
				}}
				onDragLeave={() => setIsDragging(false)}
				onDrop={(e) => {
					e.preventDefault();
					setIsDragging(false);
					handleFileChange(e.dataTransfer.files[0]);
				}}
				className={cn(
					'relative border-2 border-dashed transition-all duration-200 cursor-pointer overflow-hidden',
					isDragging ? 'border-blue-500 bg-blue-50/50' : 'border-slate-200 hover:border-slate-300',
					file ? 'border-solid border-blue-100 bg-slate-50/30' : 'p-10'
				)}
				onClick={() => !file && document.getElementById('file-input')?.click()}
			>
				<Input
					id="file-input"
					type="file"
					accept="image/jpeg,image/png"
					className="hidden"
					onChange={(e) => handleFileChange(e.target.files?.[0])}
				/>

				{!file ? (
					<div className="flex flex-col items-center text-center space-y-4">
						<div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
							<UploadCloud className="w-8 h-8" />
						</div>
						<div>
							<p className="text-sm font-bold text-slate-900">Upload Code File</p>
							<p className="text-xs text-slate-500 mt-1">Drag and drop or click to browse</p>
						</div>
						<div className="flex gap-2 text-[10px] font-bold text-slate-400">
							<span className="bg-slate-100 px-2 py-1 rounded">.js</span>
							<span className="bg-slate-100 px-2 py-1 rounded">.ts</span>
							<span className="bg-slate-100 px-2 py-1 rounded">.py</span>
							<span className="bg-slate-100 px-2 py-1 rounded">.java</span>
						</div>
					</div>
				) : (
					<div className="p-4 flex items-center gap-4">
						<div className="relative w-20 h-20 rounded-xl overflow-hidden border bg-white shrink-0">
							{preview ? (
								<div className="w-full h-full p-2 overflow-hidden text-xs font-mono text-slate-700">
									<pre className="whitespace-pre-wrap wrap-break-words">{preview.slice(0, 800)}</pre>
								</div>
							) : (
								<div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-400">
									<svg
										className="w-6 h-6"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24"
										strokeWidth="1.5"
										stroke="currentColor"
									>
										<path
											strokeLinecap="round"
											strokeLinejoin="round"
											d="M8.25 6.75h7.5M8.25 12h7.5M8.25 17.25h7.5"
										/>
									</svg>
								</div>
							)}
						</div>

						<div className="grow min-w-0">
							<p className="text-sm font-bold text-slate-900 truncate">{file.name}</p>
							<p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
							<div className="flex items-center gap-1 text-blue-600 mt-1">
								<CheckCircle2 className="w-3 h-3" />
								<span className="text-[10px] font-bold uppercase tracking-tight">Ready to Upload</span>
							</div>
						</div>

						<Button
							variant="ghost"
							size="icon"
							className="rounded-full hover:bg-red-50 hover:text-red-500 text-slate-400"
							onClick={clearFile}
						>
							<X className="w-5 h-5" />
						</Button>
					</div>
				)}
			</Card>

			{error && (
				<div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 text-red-700 text-xs font-medium border border-red-100">
					<FileWarning className="w-4 h-4 shrink-0" />
					{error}
				</div>
			)}

			<Button
				onClick={handleUpload}
				disabled={!file || loading}
				className={cn(
					'w-full h-14 rounded-2xl text-md font-bold transition-all',
					file && !loading ? 'bg-blue-600 shadow-lg shadow-blue-200' : 'bg-slate-100 text-slate-400'
				)}
			>
				{loading ? (
					<>
						<Loader2 className="mr-2 h-5 w-5 animate-spin" /> Uploading...
					</>
				) : (
					'Upload ID for Analysis'
				)}
			</Button>
		</div>
	);
}
