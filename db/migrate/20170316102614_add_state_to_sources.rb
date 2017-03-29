class AddStateToSources < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :state, :string, default: 'valid'
  end
end
