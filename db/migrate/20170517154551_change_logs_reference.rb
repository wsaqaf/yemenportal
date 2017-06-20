class ChangeLogsReference < ActiveRecord::Migration[5.0]
  def change
    SourceLog.delete_all

    remove_reference :source_logs, :source
    add_reference :source_logs, :source, null: false, foreign_key: { on_delete: :cascade }
  end
end
