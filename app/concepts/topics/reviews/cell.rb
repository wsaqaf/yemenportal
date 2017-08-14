class Topics::Reviews::Cell < Application::Cell
  private

  def reviews_page
    model
  end

  delegate :topic, :flags, :comments, :new_review_comment, to: :reviews_page
end
