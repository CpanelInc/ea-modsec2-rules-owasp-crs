# RPMify our Rules/Prep for modsec3

## Target Audiences

1. Maintenance and security teams
2. Training and technical support
3. Managers and other internal key stakeholders
4. Future project/feature owners/maintainers

## Detailed Summary

**TL;DR**: We need:

1. a better way to keep people’s rules up to date
2. to consider that modsec2 is close to EOL and 3.x is on the horizon
3. to support multiple web servers (starting w/ 3.x probably though 2 is possible).

**Details**:

We had been distributing OWASP’s Core Rule Set via WHM’s vendor YAML system.

The YAML and data was built using the [voodoo](https://enterprise.cpanel.net/projects/IDEV/repos/voodoo/browse) system.

It was ineffective because no one really understands or “owns” the system. The result? The [latest rules voodoo installs](https://github.com/coreruleset/coreruleset/releases/tag/v3.0.2) are over 3 years old at [the time of this writing](https://github.com/coreruleset/coreruleset/releases/tag/v3.3.0).

Mod Security 2 is very Apache centric so its more difficult to make it work with other web servers.

## RPMify our Rules

We need to factor in this information:

1. the current voodoo based rules are v3.0.3, and the latest as of this writing it v3.3.0
2. OWASP CRS support mod sec “2.8 on”, with some hints that they might work on 3.0 but definetly not 3.1
   * it sounds more like rules written for 3.0 will work on 2.8 but not 3.1 but 2.8 won’t work on 3.0
3. the current voodoo based rules get installed to /etc/apache2/conf.d/modsec_vendor_configs/OWASP3/
4. the actual vendor configuration that Apache uses to turn vendor rules on or off/that can be managed via WHM are in /etc/apache2/conf.d/modsec/modsec2.cpanel.conf (Owned by ea-apache24-mod_security2)
5. arbitrary custom rules are put into /etc/apache2/conf.d/modsec/modsec2.user.conf (Owned by ea-apache24-mod_security2)

### Prep for modsec3

While modsec3 design will be its own document we do need to consider some things during the RPMifying of the modsec2 rules.

For example, using this naming for rules packages:

`<PREFIX>-modsec<DIGITS>-rules-<ORGANIZATION>-<RULESET NAME>` gives us `ea-modsec2-rules-owasp-crs` now and for, say 3.1, we’d do `ea-modsec31-rules-owasp-crs`, for 3.2 `ea-modsec32-rules-owasp-crs`, ad infinitum. That also allows for other vendors, oranizations, and multiple rulesets (e.g. `alt-modsec42-comodo-free`, `alt-modsec42-comodo-pro`, etc).

The versioning would fit in w/ the v3 approach of library and connectors, e.g.:

* `ea-modsec31`
* `ea-modsec31-connector-nginx`
* `ea-modsec31-connector-apache24`

## Maintainability

Estimate:

1. how much time and resources will be needed to maintain the feature in the future
2. how frequently maintenance will need to happen

To implement, normal new package efforts (i.e. `et new`).

Once implemented, normal EA4 package maintenance (i.e. automated updates via `et update`).

## Options/Decisions

Since we have to work around existing stuff there are not a lot of options. The naming scheme seems future proof per the details above.

If the RPM installs and owns `/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/` then everything should just work w/ a minimum of changes to one UI (no API call or backend changes necessary).

The RPM needs to take over the voodoo files/configuration on install. That includes setting it to enabled and turning off updates (so the system does not try to update a thing that does not use that update system). On uninstall we don’t want to restore the backed up voodoo files because if they made any changes that are not compatible it could take Apache down.

The RPM should enable all the rulesets on install (unless there is existing OWASP3 rulesets).

On install (unless we’ve enabled all rulesets) and update we want to enable new rulesets (checking the syntax before adding).

We do not want to make the ea-apache24-mod_security2 require this ruleset because everyone has mod security so everyone would get rules they didn’t ask for, which is begging for tickets and ill will.

### Package Approaches

| Approach | Pro | Con | Notes |
| ---------|-----|-----| ----- |
| Do v3.3.0 first thing | Gets everyone updated | If there is a problem we have no easy recourse | Nope |
| Do v3.0.2 first thing, update to v3.3.0 in a few months | Should be most likely to keep working when RPM is installed | If we update to 3.3.0 and there are problems we break everyone at the same time | Nope |
| Do v3.0.2, then immedietly update to v3.3.0 | Opt in to 3.3.0 so if there is a problem we effect a minimum of servers | If there is a huge problem that doofs a tons of people we can `et rollback` to the 3.0.2 version | Opt in via CLI, UI, or feature showcase |

### Good UX on Old Versions

There are a few ULC items that could confuse users and/or cause problems if they were to use RPM based mod sec rule vendors (see CPANEL-33703 for details).

| Approach | Pro | Con | Notes |
| ---------|-----|-----| ----- |
| old versions can deal w/ bad UX, maybe backport CPANEL-33703 to 90? | very little work | older verison will have bad UX | N/A - it is what it is |
| Backport CPANEL-33703 from 92 to LTS (86) | Sane method | People who stay on old versions are unlikely to update to the new version | At least support could say, update your 86 and it won’t be weird |
| Have an RPM apply a patch of what would have been backported | All supported versions would have good UX | It is really gross to change files that belong to the ULC install | N/A - it is what it is |

### Initial Conclusion

#### Package Approach

Do v3.0.2 then immediate v3.3.0 option then make these UI changes:

`/scripts2/manage_mod_security_vendors/vendors`

1. add a table (¿above vendor based for prominence?) for RPM based rulesets:
   * if `ea-apache24-mod_security2` is installed show a row for each `<PREFIX>-modsec2-rules-<ORGANIZATION>-<RULESET NAME>` package available
   * for each `ea-modsec<DIGITS>` that is installed show a row for each `<PREFIX>-modsec<DIGITS>-rules-<ORGANIZATION>-<RULESET NAME>` package available
   * each row should have an install/uninstall button (depending on its current state)
   * we could instead use the existing pattern and show each RPM that is available but uninstalled as a row that says “this is not installed” and has an install button
2. _if they currently have our voodoo YAML bit enabled_: give them a “switch to the new hotness” button that installs the RPM (the RPM removes the voodoo bits)
3. _if they do not have our voodoo YAML bit enabled_: do not show the “want to install it?” thing (should not even have a row):
4. _if they try to install our voodoo via the YAML file_: it should error
5. The table that shows vendors, when it gets to an RPM based rule set:
  * Updates: should be disabled/clear that this is moot (ZC-7305 has a patch that makes it “RPM: Always Updated”)
  * Delete: should take them to the EA4 provision screen (ZC-7305 has a patch that does that)

#### Good UX on Old Versions

Initially, try for backport CPANEL-33703 to LTS and adjust based on pushback.

## Child Documents

None.
