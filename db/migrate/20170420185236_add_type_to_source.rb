class AddTypeToSource < ActiveRecord::Migration[5.0]
  def up
    add_column :sources, :approve_state, :string
    add_column :sources, :suggested_time, :datetime
    add_reference :sources, :user, foreign_key: true


    Source.all.each do |source|
      source.update(approve_state: 'approved') if source.approve_state.nil?
    end
  end

  def down
    remove_column :sources, :approve_state
  end
end
