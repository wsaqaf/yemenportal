class AddDeletedAtToSources < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :deleted_at, :datetime, index: true
  end
end
