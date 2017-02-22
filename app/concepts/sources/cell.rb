class Sources::Cell < Application::Cell
  def show
    render
  end

  private

  property :link

  def table_body
    concept("sources/item/cell", collection: model.to_a)
  end
end
