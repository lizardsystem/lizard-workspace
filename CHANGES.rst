Changelog of lizard-workspace
===================================================


0.17.3 (unreleased)
-------------------

- Added download link to XLS in collage screen.

- Add command and task to rename ESF layers.


0.17.2 (2012-06-21)
-------------------

- Added download links in collage screen.


0.17.1 (2012-06-21)
-------------------

- Updated popup template: it will not show "None" anymore.

- Fixed periode eigenschappen after update 0.17.


0.17 (2012-06-21)
-----------------

- Added field LayerCollage.secret_slug, timestamp_updated and migrations.

- Updated admin for LayerCollage.

- Collages are now accessible through the secret slugs.

- Added task and management command clean_temp_collages.


0.16 (2012-06-18)
-----------------

- Added collage view: statistics, grouped graphs, editable properties.

- Added statistics to LayerCollageItem plus migration.

- Added temp feature for collage.

0.15.4 (2012-06-11)
-------------------

- Update workspace_update to add location_filter to krwminimap layer.


0.15.3 (2012-06-07)
-------------------

- Add mask layer to the esf popup layerworkspaces.


0.15.2 (2012-06-07)
-------------------

- Modified workspace_update --minimap to create two layerworkspaces:
  One for areas and one for krw-waterbodies.

- Fix error in watersystem layer using deprecated geoserver layer.


0.15.1 (2012-06-06)
-------------------

- Add option --all to workspace-update management command

- Have workspace_update --minimap create the appropriate
  layerworkspace as well.


0.15 (2012-06-04)
-----------------

- Added measure layers to sync_layers.


0.14 (2012-05-31)
-----------------

- Updated LayerFolder admin with children in list view.

- Changed admin LayerFolder from filter_horizontal to filter_vertical,
  because there is a "Choose all" button now.

- Add commands for aqmad layer configuration.


0.13.1 (2012-05-29)
-------------------

- Add task and extend workspace_update command to configure a minimap layer


0.13 (2012-05-29)
-----------------

- Add task and management command to sync track record layers.

- Add task and extend workspace_update command to put track record layers
  in the right spot.



0.12 (2012-05-24)
-----------------

- Updated task sync_layers_ekr to include esf layers as well.


0.11 (2012-05-10)
-----------------

- Converted management commands to celery tasks.


0.10.1 (2012-05-04)
-------------------

- Restrict tree in appscreen to visible layers.


0.10 (2012-04-23)
-----------------

- Modify update script to reconfigure watersystem and baselayers.


0.9.8 (2012-04-20)
------------------

- Update workspace_update command to add popup classes for
  annotations and measures.


0.9.7 (2012-04-19)
------------------

- Add analyse interpretaties to workspace_update command.


0.9.6 (2012-04-17)
------------------

- Change name of layer in workspace update script for baselayers.


0.9.5 (2012-04-16)
------------------

- Add dependency on lizard_map to migration.


0.9.4 (2012-04-04)
------------------

- Improved workspace_update command
- Add layer to workspace_update command


0.9.3 (2012-04-03)
------------------

- Add general purpose management command for updating things.


0.9.2 (2012-03-22)
------------------

- Fixed bug where each synctask ran twice...


0.9.1 (2012-03-20)
------------------

- Fix sync_layers_with_wmsserver script requiring running server.


0.9 (2012-03-19)
----------------

- Nothing changed yet.


0.8.2 (2012-03-19)
------------------

- Collage api now returns 'name' as well as 'title' to ensure correct
  displaying in front end.
- Make wmsserver objects use relative paths.


0.8.1 (2012-03-19)
------------------

- Fixed bug in saving/loading collages.


0.8 (2012-03-19)
----------------

- Added grouping_hint to CollageItem.
- Fix bug in management command


0.7 (2012-03-19)
----------------

- Add exception handling and commit on success to wmssync management command.


0.6 (2012-03-16)
----------------

- Add prefix field to server model and a migration for it, too.


0.5 (2012-03-15)
----------------

- Added LayerCollageItem.name and migration.

- Added collage model functions for loading and saving collages.

- Updated sync_layers_with_wmsserver: field js_popup_class will only
  be overwritten in existing layers if layer.js_popup_class is empty
  and the server js_popup_class is not empty.

- added username and password for servers (for later implementation)

- some admin improvements

- implement selection of workspaces


0.4 (2012-03-13)
----------------

- Added models LayerCollage and LayerCollageItem and their migration.
- Add sync_layers_measure analogous to sync_layers_fewsnorm
- Add sync_layers_ekr idem


0.3 (2012-03-12)
----------------

- Added Layer.js_popup_class.

- Added Layer.is_local_layer, Layer.is_clickable,
  WmsServer.is_local_layer, WmsServer.is_clickable.

- Updated sync functions to take over the is_local_layer and
  is_clickable options.


0.2 (2012-03-08)
----------------

- Added fields to API calls.

- Implemented sync_layers_fewsnorm: it populates the Layer model with
  Layers associated with fewsnorm parameter / moduleinstance /
  qualifierset / timestep combinations.


0.1 (2012-03-06)
----------------

- See readme.

- Initial migrations.

- Initial models and api.

- Initial library skeleton created by nensskel.  [Jack Ha]
