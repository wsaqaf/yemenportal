class Moderators::Cell < Application::Cell
  private

  def table_body
    concept("moderators/item/cell", collection: model.to_a)
  end
end
