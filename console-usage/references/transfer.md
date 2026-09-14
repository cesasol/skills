# Archives, Transfer, and Disk Capacity

Every command here writes to a filesystem or another host, so each one has a read-only rehearsal: list the archive
before extracting, and dry-run the sync before copying.

## Archives

```bash
tar -tf release.tar.gz | head -n 20              # inspect before extracting
tar -xzf release.tar.gz -C build/                # extract into a directory that exists
tar -czf release.tar.gz -C dist .                # archive the contents of dist, not the path to it
tar --zstd -cf release.tar.zst -C dist .         # zstd, where the tar build supports it
tar -xf release.tar.zst -C build/                # modern tar detects the compression
tar --strip-components=1 -xzf upstream.tar.gz -C src/
```

`-C` before the paths keeps absolute or parent-relative directory names out of the archive. An archive that expands
into the current directory instead of a single top-level folder is a tarbomb; that is exactly what `tar -tf` reveals
and why the listing comes first.

```bash
zstd -19 -T0 backup.sql                          # maximum ratio, all cores
unzstd backup.sql.zst
unzip -l bundle.zip                              # list first
unzip -q bundle.zip -d build/
```

GNU tar and BSD tar disagree about several flags, `--zstd` among them. When a flag is rejected, check `tar --help`
rather than assuming the archive is broken, and fall back to a pipeline: `zstd -dc file.tar.zst | tar -xf -`.

## rsync

```bash
rsync -a --dry-run --itemize-changes src/ dest/          # rehearse, and show exactly what would change
rsync -a --info=progress2 src/ dest/                     # then copy
rsync -a --exclude '.git/' --exclude 'node_modules/' src/ dest/
rsync -a -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' src/ host:/srv/app/
rsync -a --delete --dry-run src/ dest/                   # never run --delete without seeing this output first
```

The trailing slash decides the outcome. `rsync -a src/ dest/` copies the contents of `src` into `dest`; `rsync -a src
dest/` creates `dest/src`. One missing character is the difference between a sync and a nested duplicate, and with
`--delete` it is the difference between a sync and data loss.

`-a` implies recursion and preserves permissions, times, symlinks, and ownership; ownership is preserved only when
running as root. Add `-z` for a slow link, and prefer rsync over `scp` because it is resumable, verifiable, and can
rehearse.

## ssh in Batch Mode

```bash
ssh -n -o BatchMode=yes -o ConnectTimeout=10 host 'systemctl is-active nginx'
ssh -n -o BatchMode=yes host 'cat /etc/os-release' | grep '^VERSION_ID='
```

`BatchMode=yes` turns every password or passphrase prompt into an immediate failure, `ConnectTimeout` bounds the
handshake, and `-n` detaches stdin so a remote command cannot swallow the local script's input. Host-key prompts fail
the same way; accepting an unknown host key is the user's decision, so report it rather than passing
`StrictHostKeyChecking=no`.

## Disk Capacity

```bash
df -h /                                 # free space by filesystem
df -i /                                 # free inodes, the failure that df -h hides
dust -bP -d 2 /var                      # where the space went
fd -t f -S +100m . /var/log             # the large files themselves
```

A write that fails with "no space left on device" while `df -h` shows free space is usually inode exhaustion, a
filesystem quota, or space held by a deleted file that a process still has open. `df -i` answers the first;
`lsof +L1` answers the third where it is installed.

## Edge Cases and Mistakes

- **`rsync --delete` pointed at the wrong path.** The most destructive command in this file. Dry-run first, every time,
  and read the itemized output before removing `--dry-run`.
- **A missing trailing slash.** The result is `dest/src/src` or a copy in the wrong place. Check the rehearsal output.
- **The archive exploded into the current directory.** A tarbomb. `tar -tf` first; extract with `-C` into a new
  directory.
- **Absolute paths inside a tarball.** GNU tar strips the leading slash and warns; never extract such an archive
  without reading the listing.
- **Permissions or ownership are not preserved.** Ownership needs root. Say so rather than suggesting `sudo`.
- **An interrupted transfer.** rsync resumes; `scp` and `tar` over a pipe do not. Re-run rsync with the same arguments.
- **ssh hangs.** A prompt for a password or an unknown host key. Add `BatchMode=yes` and `ConnectTimeout`, then report
  what the prompt wanted.
- **Filenames with spaces or newlines.** Use `rsync --files-from=-` with a NUL-safe generator, or `fd -0` with
  `xargs -0`; never build a copy command from unquoted output.
- **Out of space mid-copy.** Check `df -h` and `df -i` before a large transfer, and clean up the partial destination so
  a retry does not run into the remains of the failed attempt.
