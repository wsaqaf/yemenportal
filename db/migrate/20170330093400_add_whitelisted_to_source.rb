class AddWhitelistedToSource < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :whitelisted, :boolean, default: false
  end
end
