class Posts::VoteUpdater
  def initialize(user, post)
    @user = user
    @post = post
  end

  def upvote
    if vote.present?
      vote.make_upvote
    else
      Vote.create_upvote(user: user, post: post)
    end
    update_post_voting_result
  end

  def downvote
    if vote.present?
      vote.make_downvote
    else
      Vote.create_downvote(user: user, post: post)
    end
    update_post_voting_result
  end

  def delete
    vote.destroy
    update_post_voting_result
  end

  private

  attr_reader :user, :post

  def vote
    Vote.find_by(user: user, post: post)
  end

  def update_post_voting_result
    post.update_voting_result(voting_result_for_post)
  end

  def voting_result_for_post
    Vote.voting_result_for(post)
  end
end
