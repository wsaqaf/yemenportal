class CreateSources < ActiveRecord::Migration[5.0]
  def change
    create_table :sources do |t|
      t.string :link, null: false

      t.timestamps
    end
  end
end
