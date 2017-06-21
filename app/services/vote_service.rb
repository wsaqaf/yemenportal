class VoteService
  UPVOTE = "upvote".freeze
  BUTTON_TYPE = { upvote: "upvote", downvote: "downvote" }.freeze

  def self.make_vote(params, user)
    post = Post.find(params.fetch(:post_id))
    vote = Vote.find_by(user: user, post: post)
    type = params[:type] == UPVOTE

    if vote
      old_type = vote.positive ? BUTTON_TYPE[:upvote] : BUTTON_TYPE[:downvote]
      vote.positive == type ? vote.delete : vote.update(positive: type)
      return old_type
    else
      Vote.create(user: user, positive: type, post: post)
      return "new"
    end
  end
end
