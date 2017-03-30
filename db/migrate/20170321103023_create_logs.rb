class CreateLogs < ActiveRecord::Migration[5.0]
  def change
    create_table :source_logs do |t|
      t.string :state
      t.references :source, null: false, foreign_key: true
      t.integer :posts_count, default: 0

      t.timestamps
    end
  end
end
