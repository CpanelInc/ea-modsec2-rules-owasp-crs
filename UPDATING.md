# 📌 Additional Update Considerations

When performing an `et update`, please keep the following steps and dependencies in mind:

1. **Metadata Synchronization**
   - All metadata is updated to reflect the current values during the `et update` process.

2. **Triggering a Change for `ea-modsec30-rules-owasp-crs`**
   - An `et change` is initiated for `ea-modsec30-rules-owasp-crs`.
   - This includes building the package on OBS (Open Build Service).

3. **Dependency on `ea-modsec2-rules-owasp-crs`**
   - The change for `ea-modsec30-rules-owasp-crs` **cannot be completed** until the corresponding update to `ea-modsec2-rules-owasp-crs` has been **merged into the `main` branch**. And **built on `EA4`**.

4. **Finalizing the Build**
   - Once `ea-modsec2-rules-owasp-crs` is merged to `main` and **built on `EA4`**, you must run:
     ```bash
     cd ~/git/ea-modsec30-rules-owasp-crs
     et obs --watch
     ```
   - This completes the build and deployment process for `ea-modsec30-rules-owasp-crs`.
