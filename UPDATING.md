# Additional update considerations

After this package is updated via `et update` the following will also need to be done:

1. Update the version in SOURCES/meta_OWASP3.yaml
2. Add the list of new rule sets to SOURCES/new_includes.yaml
   * the format is explained at the top of the file in a comment
      * add the version as a new key
      * add the list of new files (name only) as its value
   * if there are no new rule sets this file does not need changed

Some ideas to consider:

1. Build SOURCES/meta_OWASP3.yaml in the SPEC file so it does not not need updated.
2. Have a script that updates SOURCES/new_includes.yaml for us.
3. Have 1 and 2 be automatic and make this document moot by implementing ZC-7313.
4. If possible, get the version they were on at the beginning of the transaction and step though all versions’ new rule sets (i.e. instead of just the newest one).

