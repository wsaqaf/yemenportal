class Search::Cell < Application::Cell
  property :posts
  option :user_votes, :user, :request_text

  private

  def post_body
    if model.empty?
      t("post.search.empty_result")
    else
      concept("posts/approved/item/cell", collection: model, user_votes: user_votes, user: user)
    end
  end
end
