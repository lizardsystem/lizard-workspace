Changelog of lizard-workspace
===================================================


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
