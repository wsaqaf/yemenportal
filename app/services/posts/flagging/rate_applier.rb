class Posts::Flagging::RateApplier
  def initialize(post)
    @post = post
  end

  def add_rate(rate)
    post.update(review_rating: post.reload.review_rating + rate)
  end

  def subtract_rate(rate)
    post.update(review_rating: post.reload.review_rating - rate)
  end

  private

  attr_reader :post
end
