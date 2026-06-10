const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function main() {
  const cats = await Promise.all([
    prisma.category.upsert({ where:{slug:'electronics'}, update:{}, create:{name:'إلكترونيات',slug:'electronics',icon:'💻'}}),
    prisma.category.upsert({ where:{slug:'clothing'}, update:{}, create:{name:'ملابس',slug:'clothing',icon:'👕'}}),
    prisma.category.upsert({ where:{slug:'home'}, update:{}, create:{name:'المنزل',slug:'home',icon:'🏠'}}),
    prisma.category.upsert({ where:{slug:'sports'}, update:{}, create:{name:'رياضة',slug:'sports',icon:'⚽'}}),
    prisma.category.upsert({ where:{slug:'books'}, update:{}, create:{name:'كتب',slug:'books',icon:'📚'}}),
  ]);
  const [electronics, clothing, home, sports, books] = cats;

  const products = [
    { name:'سماعات لاسلكية بلوتوث', slug:'wireless-headphones', description:'سماعات عالية الجودة مع إلغاء الضوضاء وبطارية 30 ساعة. صوت نقي وتصميم أنيق مريح.', price:299, originalPrice:450, stock:15, featured:true, categoryId:electronics.id, images:JSON.stringify(['https://picsum.photos/seed/headphones1/600/600','https://picsum.photos/seed/headphones2/600/600']) },
    { name:'ساعة ذكية رياضية', slug:'smart-watch', description:'ساعة ذكية مقاومة للماء تتابع نشاطك اليومي ونبضات القلب. شاشة AMOLED واضحة.', price:599, originalPrice:799, stock:8, featured:true, categoryId:electronics.id, images:JSON.stringify(['https://picsum.photos/seed/watch1/600/600','https://picsum.photos/seed/watch2/600/600']) },
    { name:'لاب توب احترافي', slug:'pro-laptop', description:'معالج i7 الجيل الثالث عشر، رام 16GB، SSD 512GB. أداء استثنائي للعمل والترفيه.', price:3499, originalPrice:4200, stock:3, featured:true, categoryId:electronics.id, images:JSON.stringify(['https://picsum.photos/seed/laptop1/600/600','https://picsum.photos/seed/laptop2/600/600']) },
    { name:'مكبر صوت بلوتوث محمول', slug:'bluetooth-speaker', description:'صوت قوي ومقاوم للماء IP67. بطارية 20 ساعة، مثالي للرحلات.', price:179, originalPrice:250, stock:18, featured:false, categoryId:electronics.id, images:JSON.stringify(['https://picsum.photos/seed/speaker1/600/600']) },
    { name:'قميص قطني كلاسيكي', slug:'classic-shirt', description:'قطن 100% بقصة كلاسيكية مريحة. مناسب للمناسبات الرسمية وغير الرسمية.', price:89, originalPrice:120, stock:30, featured:false, categoryId:clothing.id, images:JSON.stringify(['https://picsum.photos/seed/shirt1/600/600','https://picsum.photos/seed/shirt2/600/600']) },
    { name:'جاكيت رياضي للشتاء', slug:'winter-jacket', description:'جاكيت دافئ مقاوم للرياح. مناسب للرياضة الخارجية في الجو البارد.', price:320, originalPrice:420, stock:12, featured:false, categoryId:clothing.id, images:JSON.stringify(['https://picsum.photos/seed/jacket1/600/600']) },
    { name:'فستان صيفي أنيق', slug:'summer-dress', description:'فستان خفيف من الشيفون. مناسب للمناسبات والتنزه.', price:155, originalPrice:210, stock:22, featured:false, categoryId:clothing.id, images:JSON.stringify(['https://picsum.photos/seed/dress1/600/600']) },
    { name:'كرسي مكتب مريح', slug:'office-chair', description:'كرسي ظهر قابل للتعديل ومسند ذراعين. مثالي للعمل من المنزل.', price:850, originalPrice:1100, stock:5, featured:true, categoryId:home.id, images:JSON.stringify(['https://picsum.photos/seed/chair1/600/600','https://picsum.photos/seed/chair2/600/600']) },
    { name:'مجموعة أدوات المطبخ', slug:'kitchen-set', description:'12 قطعة استانلس ستيل. مجارف وملاعق ومقصات.', price:199, originalPrice:280, stock:25, featured:false, categoryId:home.id, images:JSON.stringify(['https://picsum.photos/seed/kitchen1/600/600']) },
    { name:'وسادة ذاكرة فوم', slug:'memory-foam-pillow', description:'وسادة طبية تدعم الرقبة وتريح العمود الفقري.', price:120, originalPrice:160, stock:40, featured:false, categoryId:home.id, images:JSON.stringify(['https://picsum.photos/seed/pillow1/600/600']) },
    { name:'حذاء رياضي خفيف', slug:'sports-shoe', description:'حذاء رياضي للجري والتمارين. نعل مرن وشبكة تهوية ممتازة.', price:249, originalPrice:349, stock:20, featured:false, categoryId:sports.id, images:JSON.stringify(['https://picsum.photos/seed/shoe1/600/600','https://picsum.photos/seed/shoe2/600/600']) },
    { name:'حقيبة رياضية كبيرة', slug:'sports-bag', description:'حقيبة متعددة الجيوب للصالة والرحلات. مقاومة للماء.', price:185, originalPrice:240, stock:16, featured:false, categoryId:sports.id, images:JSON.stringify(['https://picsum.photos/seed/bag1/600/600']) },
    { name:'حبل القفز الاحترافي', slug:'jump-rope', description:'حبل قفز سريع بمقابض مريحة. مناسب للبوكسينغ والكارديو.', price:45, originalPrice:65, stock:50, featured:false, categoryId:sports.id, images:JSON.stringify(['https://picsum.photos/seed/rope1/600/600']) },
    { name:'فن التفكير الواضح', slug:'clear-thinking-book', description:'52 خطأ شائعاً في التفكير وكيفية تجنبها. طبعة عربية منقحة.', price:65, originalPrice:85, stock:50, featured:false, categoryId:books.id, images:JSON.stringify(['https://picsum.photos/seed/book1/600/600']) },
    { name:'الذكاء الاصطناعي للمبتدئين', slug:'ai-book', description:'دليل شامل لأساسيات الذكاء الاصطناعي وتطبيقاته.', price:75, originalPrice:100, stock:40, featured:false, categoryId:books.id, images:JSON.stringify(['https://picsum.photos/seed/book2/600/600']) },
    { name:'العادات الذرية', slug:'atomic-habits', description:'كتاب بيست سيلر عالمي عن بناء عادات صغيرة تحدث تغييراً كبيراً.', price:70, originalPrice:95, stock:35, featured:true, categoryId:books.id, images:JSON.stringify(['https://picsum.photos/seed/book3/600/600']) },
  ];

  for (const p of products) {
    await prisma.product.upsert({ where:{slug:p.slug}, update:p, create:p });
  }

  const adminPass = await bcrypt.hash('admin123', 10);
  const userPass  = await bcrypt.hash('user123', 10);

  const admin = await prisma.user.upsert({
    where:{email:'admin@store.com'}, update:{},
    create:{ name:'المدير', email:'admin@store.com', password:adminPass, role:'ADMIN', phone:'0500000000' }
  });
  const customer = await prisma.user.upsert({
    where:{email:'user@store.com'}, update:{},
    create:{ name:'أحمد محمد', email:'user@store.com', password:userPass, phone:'0551234567' }
  });

  const allProducts = await prisma.product.findMany();
  const reviewData = [
    { rating:5, comment:'منتج رائع جداً، جودة ممتازة وسعر مناسب' },
    { rating:4, comment:'جيد جداً، التوصيل كان سريعاً والمنتج مطابق للوصف' },
    { rating:5, comment:'أنصح به بشدة! خدمة عملاء ممتازة' },
  ];
  for (let i = 0; i < Math.min(3, allProducts.length); i++) {
    await prisma.review.upsert({
      where:{ userId_productId:{ userId:customer.id, productId:allProducts[i].id } },
      update:{},
      create:{ userId:customer.id, productId:allProducts[i].id, ...reviewData[i] }
    });
  }

  console.log('✅ Seed complete');
  console.log('Admin: admin@store.com / admin123');
  console.log('User:  user@store.com  / user123');
}

main().catch(console.error).finally(() => prisma.$disconnect());
