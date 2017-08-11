class Topics::Reviews::Cell < Application::Cell
  private

  def topic
    reviews_page.topic
  end

  def reviews_page
    model
  end

  def flags
    reviews_page.flags
  end
end
