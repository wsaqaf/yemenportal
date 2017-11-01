class RemoveWhitelistedFieldOfSource < ActiveRecord::Migration[5.0]
  def change
    remove_column :sources, :whitelisted
  end
end
