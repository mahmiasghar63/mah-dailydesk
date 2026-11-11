# Windows Authenticode code signing

**Status:** GitHub Actions signing integration is prepared, but **no signing publisher is connected yet**. MAH DailyDesk v1.0.0 was built before this change and **is unsigned**. It must not be described as signed.

The release workflow now **fails closed**: it refuses to create any *new* release until a verified signing provider is configured, signs the Windows executable and its Authenticode signature and RFC 3161 timestamp verify. It also produces a GitHub build-provenance attestation for the packaged ZIP. Signing occurs after the frozen EXE startup check and before ZIP creation and checksum generation. The existing v1.0.0 assets will not be rewritten.

## Recommended for an eligible open-source project: SignPath Foundation

SignPath Foundation offers free code signing for qualifying maintained, released, open-source projects, subject to its own application, review and signing policies: https://signpath.org/ . The Foundation is the named publisher for signatures issued under its certificate. Acceptance is **not guaranteed**.

1. Apply to SignPath Foundation for MAH DailyDesk with the public repository https://github.com/mahmiasghar63/mah-dailydesk . Do not misrepresent your identity, ownership or eligibility.
2. Upon approval, configure its GitHub.com trusted build system, connect the repository with the SignPath GitHub App and create a SignPath project, an EXE Authenticode artifact configuration, and a release-signing policy limited to trusted builds from `main`. Follow https://docs.signpath.io/trusted-build-systems/github .
3. In GitHub **Settings → Secrets and variables → Actions**, add **one repository secret**: `SIGNPATH_API_TOKEN` (a restricted SignPath token granted permission to submit signing requests).
4. Add repository **variables**: `SIGNING_PROVIDER=signpath`, `SIGNPATH_ORG` (SignPath organization ID), `SIGNPATH_PROJECT` (project slug), `SIGNPATH_POLICY` (release policy slug), and optionally `SIGNPATH_ARTIFACT_CONFIG` (artifact configuration slug, if it is not the project default).
5. Approve signing requests as required by your SignPath policy. Only the returned, signed `MAH-DailyDesk.exe` is packaged into the release. The workflow refuses to publish when signing or verification fails.

**Never upload a signing key or API token to Git, an issue, or a chat.** The SignPath Foundation signature identifies the Foundation as publisher, not the author's personal name.

## Alternative: Azure Artifact Signing (where eligible)

Microsoft's public-trust onboarding has geographic and billing eligibility limits. Consult https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart before relying on it. A paid Azure subscription, eligible publisher identity validation, Artifact Signing account and certificate profile may be required. **Public Trust is not currently offered to individual publishers based in Pakistan**, per Microsoft's published regional eligibility list. Do not misrepresent location or identity to work around eligibility.

For an eligible, legitimately verified Azure signing account:

1. Configure an Entra application and GitHub OIDC federation specifically for `repo:mahmiasghar63/mah-dailydesk:ref:refs/heads/main`, and grant only the `Artifact Signing Certificate Profile Signer` role required for signing.
2. Add GitHub Actions repository **secrets** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` (identifiers that are used by the OIDC login action; no Azure client password is used).
3. Add repository **variables** `SIGNING_PROVIDER=azure`, `SIGNING_ENDPOINT` (matching your account's regional HTTPS endpoint), `SIGNING_ACCOUNT` and `SIGNING_PROFILE`.
4. Build a **new version**, not v1.0.0, after Azure identity validation and signing access are working. The Azure service signs with keys protected by the managed service rather than storing a private key in GitHub.

See https://github.com/Azure/artifact-signing-action and https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure .

## Verification and release policy

Only a successful trusted signing request can produce a new public release. The Windows runner runs `Get-AuthenticodeSignature` and requires a valid trusted signature, a timestamping certificate, and the Code Signing certificate EKU before packaging. The release ZIP is also hashed with SHA-256 and receives a GitHub build-provenance attestation (which is **separate** from Windows Authenticode signing).

To inspect a signed future release after extracting it, run:

```powershell
Get-AuthenticodeSignature .\MAH-DailyDesk\MAH-DailyDesk.exe | Format-List Status,SignerCertificate,TimeStamperCertificate
```

The result must show `Status : Valid`. Verify the downloaded ZIP checksum against the release's `SHA256SUMS.txt` too. A signature establishes publisher integrity, not that software is guaranteed malware-free or warning-free. A new version requires updating `release/VERSION`, `dailydesk/__init__.py`, `pyproject.toml`, and release notes. Do **not** republish or re-sign the unchanged v1.0.0 under the same tag.
